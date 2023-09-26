
        # with open('web_page.html', 'w', encoding='utf-8') as f:
        #     f.write(self.driver.page_source)

        products = self.driver.find_elements(
            By.CLASS_NAME, "sh-dgr__grid-result")

        for index, product in enumerate(products):
            if (index > config.max_search_results):
                break
            tmp = {}

            divs = product.find_elements(By.TAG_NAME, "div")
            imgs = product.find_elements(By.TAG_NAME, "img")
            links = product.find_elements(By.TAG_NAME, "a")

            print("\n#################\n")
            # print(divs)

            tmp["text"] = []
            for div in divs:
                # print(div.get_attribute("class"))
                # print(div.text)
                # print(div.get_attribute("class"))
                # if div.get_attribute("class") == "EI11Pd":
                print(div.get_attribute("class"))
                print(div.text)

                # i0X6df : All Descriptopn Text
               
               ## EI11Pd : Title
               
               ## NzUzee : Rating
                #        : Number of Ratings
                #        : Out of & Summary
                
                # dWRflb : additional info
                
                # zLPF4b : Price description
                #        : price
                #        : store
                #        : shipping

               ## XrAfOe : price & mrp
               
               ## IuHnof : store 
                # aULzUe : store
               
               ## bONr3b : shipping




                # sh-dgr__content : Price

                if div.get_attribute("class") == "sh-dgr__content":
                    #     print(div.text)
                    tmp["text"].append(div.text)
                #     time.sleep(0.1)
            tmp["img"] = []
            for img in imgs:
                # print(img.get_attribute("src"))
                # tmp["img"].append("<img src='"+img.get_attribute("src")+"'>")
                tmp["img"].append(img.get_attribute("src"))
            tmp["link"] = []
            for link in links:
                # print(link.get_attribute("href"))
                tmp["link"].append(link.get_attribute("href"))

            self.product_data.append(tmp)